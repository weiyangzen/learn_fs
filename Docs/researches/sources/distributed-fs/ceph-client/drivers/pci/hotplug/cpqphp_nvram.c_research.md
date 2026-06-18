# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.c

## Purpose
Implements optional Compaq NVRAM persistence for hotplug resource lists. It reads and invalidates a BIOS environment variable at startup, overlays persisted free resource pools onto the active controller, and writes current free resources back on module unload through a Compaq INT15 ROM entry point.

## Important APIs, Types, and Functions
Important constants are `ROM_INT15_PHY_ADDR`, `READ_EV`, and `WRITE_EV`. Persistent formats are `struct ev_hrt_header` and `struct ev_hrt_ctrl`; `struct register_foo` and `struct all_reg` describe the low-level BIOS call register model but are not used by the inline assembly wrapper. Global state includes `evbuffer_init`, `evbuffer_length`, `evbuffer[1024]`, `compaq_int15_entry_point`, and `int15_lock`. Public functions are `compaq_nvram_init()`, `compaq_nvram_load()`, and `compaq_nvram_store()`. Internal helpers are `add_byte()`, `add_dword()`, `check_for_compaq_ROM()`, `access_EV()`, `load_HRT()`, and `store_HRT()`.

## Control Flow
Core probe calls `compaq_nvram_init()` after ROM mapping to compute the INT15 entry pointer. Resource discovery calls `compaq_nvram_load()` once globally; it reads `CQTHPS`, invalidates the old variable by writing `0xff`, validates version/controller identity, and appends persisted memory, prefetchable memory, I/O, and bus nodes to the matching controller's free lists. Module unload calls `compaq_nvram_store()`, which serializes each controller identity and resource-list counts/data into `evbuffer` and writes `CQTHPS` back through `access_EV()`.

## State and Persistence Behavior
This is the only Compaq file in the set that intentionally persists driver state beyond runtime. The persisted state is not slot config, but free resource pools per controller. `evbuffer_init` prevents repeated ROM reads. `evbuffer_length` bounds parsing, and the 1024-byte buffer caps serialized state. `access_EV()` serializes firmware calls with a spinlock and disables interrupts around the far call-like ROM entry invocation.

## Dependencies and Integration Points
Depends on `cpqphp.h` global controller/resource structures, the legacy ROM mapping from `cpqphp_core.c`, Compaq ROM OEM string at `0xffea`, x86 inline assembly, and BIOS support for `READ_EV`/`WRITE_EV` environment variable operations. It is compiled only when `CONFIG_HOTPLUG_PCI_COMPAQ_NVRAM` enables the real declarations from `cpqphp_nvram.h`.

## Risks
Calling BIOS code from the kernel is architecture- and firmware-sensitive. The parser casts unaligned bytes to `u32 *`, depends on a small fixed buffer, and trusts count fields except for length checks. `evbuffer_length` is `u8`, so a 1024-byte transfer length truncates. Persisted stale or corrupt resources can affect future hot-add allocation. Firmware call failures fall back to ROM/HRT resources but can silently lose previous resource state.

## Test Signals
Build with and without `CONFIG_HOTPLUG_PCI_COMPAQ_NVRAM`, Compaq ROM detection, INT15 READ/WRITE success and failure, invalid/corrupt/truncated `CQTHPS`, version 1 versus version 2 data, matching and nonmatching controller identities, resource-list sort after load, unload store with multiple controllers, and behavior when serialized data exceeds 1024 bytes.
