# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/chip.h

Purpose: HFI1 chip-facing contract header. It collects hardware dimensions, packet buffer control fields, interrupt source numbering, link-state and 8051 firmware constants, resource-lock bits, receive/transmit counter indexes, CSR access helpers, and prototypes for chip, firmware, interrupt, counter, link, QSFP, and context management code.

Important APIs/types: `read_csr()`, `write_csr()`, `read_kctxt_csr()`, `write_kctxt_csr()`, `read_uctxt_csr()`, `write_uctxt_csr()`, `get_csr_addr()`, `create_pbc()`, `acquire_chip_resource()`, `release_chip_resource()`, `set_link_state()`, `start_freeze_handling()`, `update_usrhead()`, `hfi1_read_cntrs()`, interrupt handlers, and `struct is_table` are the major exported surfaces. The `C_*` counter enums are shared indexes for device and port counter arrays and must stay aligned with counter read code.

Control flow: there is no body-level control flow beyond inline CSR address calculation and VL/index conversion. Runtime control flow is defined by call contracts: chip code reads capability CSRs, programs context CSRs with kernel or user spacing, arbitrates ASIC shared resources through scratch bits and mutexes, transitions link state through workqueue handlers, and dispatches interrupts using source ranges and `is_table` entries.

State and persistence: the header describes persistent hardware state in CSRs, 8051 data memory/config fields, ASIC scratch resource flags, PBC words, RcvArray/TID entries, and per-VL counters. Software persistence is indirect through `struct hfi1_devdata`, `struct hfi1_pportdata`, and `struct hfi1_ctxtdata` fields manipulated by the declared functions.

Dependencies and integration: includes `chip_registers.h` and relies on kernel bit macros plus HFI1 core structs from other headers. Nearly every HFI1 implementation file consumes these definitions, so it is the central integration point between register metadata, firmware loading, link management, receive handling, send DMA, debugfs, and counter export.

Risks: ABI drift in bit masks, enum order, interrupt ranges, or CSR spacing can corrupt hardware programming without compiler errors. The distinction between 0x100 kernel-context CSR spacing and 0x1000 user-context spacing is safety critical because user-mappable CSRs must not expose adjacent contexts. Resource bits in ASIC scratch are shared between HFI instances and OSes, so incorrect acquisition/release can deadlock or race external firmware/QSFP/EPROM access.

Test signals: build coverage across the whole driver, register trace review during probe, counter name/value alignment tests, interrupt source remapping tests, link bringup/down testing, resource lock contention tests on dual-HFI devices, and receive/send smoke tests that validate the PBC/RHF/TID field constants.
