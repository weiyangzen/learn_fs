<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Makefile

## Purpose
The `Makefile` assembles the Intel ISH driver family into separate kernel objects for the ISHTP bus/core, IPC PCI transport, HID client, and optional firmware loader.

## Important APIs, Types, and Functions
`intel-ishtp.o` includes ISHTP initialization, host bus management, client handling, bus registration, DMA interface, client buffers, and loader infrastructure. `intel-ish-ipc.o` includes hardware IPC and PCI glue. `intel-ishtp-hid.o` includes HID glue and the HID ISHTP client. `intel-ishtp-loader.o` includes the host firmware loader when configured. `ccflags-y` adds the local `ishtp` include directory.

## Control Flow
There is no runtime flow. Kconfig symbols decide which composite objects are linked. Splitting IPC, bus, HID, and loader objects allows the base transport and HID stack to be built independently from host firmware loading.

## State and Persistence Behavior
The file controls build products only. Object grouping determines module boundaries and symbol visibility interactions between the ISHTP bus exports, IPC transport, and client drivers.

## Dependencies and Integration Points
The object lists must stay synchronized with source-level exports and headers. The include path allows files outside `ishtp/` to include private transport headers such as `bus.h`.

## Risks and Edge Cases
Missing an object silently breaks link-time symbols or runtime functionality. Moving source files without updating composite object lists can make configured modules incomplete. Because the HID and loader clients register through late init calls, module boundaries and init order matter.

## Test Signals
Build `INTEL_ISH_HID=y/m` and `INTEL_ISH_FIRMWARE_DOWNLOADER=y/m`; verify modules contain expected objects; run modpost for unresolved symbols; and boot-test that PCI probe creates ISHTP bus clients and HID devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Makefile -->
