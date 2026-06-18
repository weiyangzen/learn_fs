# sources/distributed-fs/ceph-client/drivers/scsi/ppa.h

## Purpose
`ppa.h` is the private hardware-access header for the Iomega PPA3 parallel-port SCSI driver. It defines version/history metadata, transfer mode constants, timing/burst parameters, register access macros, and the internal `ppa_engine()` prototype used by `ppa.c`.

## Important APIs, types, and functions
The header defines mode constants `PPA_AUTODETECT`, `PPA_NIBBLE`, `PPA_PS2`, `PPA_EPP_8`, `PPA_EPP_16`, `PPA_EPP_32`, and `PPA_UNKNOWN`, plus `PPA_MODE_STRING`. Tunables include `PPA_BURST_SIZE`, `PPA_SELECT_TMO`, `PPA_SPIN_TMO`, `PPA_RECON_TMO`, and `PPA_DEBUG`. `IN_EPP_MODE()` identifies EPP variants. Register access macros wrap `inb()` and `outb()` for DTR, status, control, EPP data, FIFO, and ECR registers; `w_ctr()` optionally uses `outb_p()` when `CONFIG_SCSI_IZIP_SLOW_CTR` is enabled.

## Control flow relevance
`ppa.c` uses these constants to select transfer paths, set delays, poll ready/status bits, and drive the connect/disconnect/select handshakes. The register macros are the only abstraction between the protocol engine and hardware I/O ports.

## State and persistence behavior
No persistent state is stored here. The static `PPA_MODE_STRING` array has internal linkage because it is included directly by `ppa.c`. Runtime state lives in `ppa_struct` from `ppa.c`; this header only defines constants and I/O access forms.

## Dependencies and integration points
The header depends on Linux kernel headers for modules, I/O resources, delays, proc support, interrupts, SCSI host definitions, and architecture I/O. It must be included after `ppa_struct` is defined because it declares `ppa_engine(ppa_struct *, struct scsi_cmnd *)`.

## Risks and test signals
Risks include architecture dependence on port I/O, macro side effects, mode string array mutability, and timing constants that are empirical rather than negotiated. Validation should include compile coverage for both slow and normal control-port writes, transfer-mode selection tests, and hardware or emulated tests that exercise status/control bit transitions.
