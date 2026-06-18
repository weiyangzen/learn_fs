# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.h

## Purpose

`fman.h` is the internal/public interface for the DPAA Frame Manager driver family. It exposes frame descriptor status and command bits, buffer prefix layout structures, buffer pool/depletion descriptors, FMan exception and interrupt enums, core driver structs, port initialization parameters, and the exported APIs implemented by `fman.c`.

## Important APIs, Types, And Functions

Important definitions include frame descriptor command bits (`FM_FD_CMD_*`) and RX/TX/parser/keygen error bits (`FM_FD_ERR_*`), resource constants such as `FMAN_BMI_FIFO_UNITS`, `BM_MAX_NUM_OF_POOLS`, and `MAX_NUM_OF_MACS`, and the opaque `struct fman`. `struct fman_prs_result` describes the parser result layout passed in buffer prefix context. `struct fman_buffer_prefix_content`, `struct fman_ext_pools`, and `struct fman_buf_pool_depletion` define buffer layout and BMan depletion policy inputs shared with port code.

The file defines `enum fman_exceptions`, `enum fman_event_modules`, `enum fman_intr_type`, and `enum fman_inter_module_event`, plus callback typedefs `fman_exceptions_cb` and `fman_bus_error_cb`. `struct fman_dts_params`, `struct fman`, and `struct fman_port_init_params` form the main cross-file data contract.

## Control Flow

No executable flow exists here, but the header dictates the call sequence among modules. Platform probe constructs `struct fman`; MAC drivers register interrupt callbacks with `fman_register_intr()`; port drivers pass resource needs through `fman_set_port_params()`; MAC drivers synchronize max frame length through `fman_set_mac_max_frame()`; and consumers query clock, FIFO limits, QMan channels, memory resource, max frame size, and RX headroom through getters.

## State And Persistence Behavior

`struct fman` owns MMIO register pointers, callback slots, a spinlock, runtime `state`, temporary `cfg`, MURAM allocator, KeyGen handle, CAM/FIFO MURAM offsets, saved LIODN tables, and parsed device-tree parameters. The header only forward-declares several internal register/state types, keeping most implementation details private to `fman.c` while allowing pointer storage.

## Dependencies And Integration Points

The header depends on Linux IO, interrupt, and OF IRQ types. It is included by MAC implementations, port code, MURAM/keygen users indirectly, and any FMan consumer needing exported APIs. The frame descriptor and parser-result definitions integrate with DPAA datapath buffer handling outside this subset.

## Risks And Edge Cases

Because this header exposes concrete `struct fman`, many implementation fields become visible across compilation units, increasing coupling. `MAX_NUM_OF_MACS` and `FMAN_EV_CNT` fix array sizes used by interrupt dispatch and max-frame tracking. Enum-to-bit mappings are implemented separately in `fman.c`; any enum changes must update those mappings. The parser-result structure relies on exact hardware layout and endian annotations.

## Test Signals

Compile tests should cover all includers and configurations for `CONFIG_DPAA_ERRATUM_A050385`. ABI-like checks should verify parser-result and port-parameter sizes against hardware expectations. Integration tests should ensure MAC and port callers obey the declared port id, max-frame, and callback contracts.
