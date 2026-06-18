# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-prph.h

Purpose: Defines internal peripheral-register addresses and bitfields for power management, NMI/reset, scheduler, FIFOs, radio access, firmware monitor, OTP/MAC identity, debug, CNVI/CNVR, sleep, and indirect access paths.

Important APIs and definitions: Constants cover APMG clock/power/RF-kill registers, device system time and NMI doorbells, shared APMG registers, SCD scheduler memory/register layout, RX/TX FIFO pointers, radio read commands, LTR controls, monitor buffer registers, WFPM/WFMP MAC and OTP registers, CPU status/current PC, firmware sequence version registers, UMAC doorbells, WMAL indirect reads, and device-family identification macros.

Control flow: No executable code. Other files use these constants with IO/PRPH helpers to power devices, release CPUs, configure schedulers, trigger NMIs/reset handshakes, read MAC addresses, collect debug monitor data, and inspect firmware status.

State and persistence: Owns no C state; defines hardware state locations. Many registers survive or reset across different reset levels, so comments identify reset-sensitive locations such as ucode-load status.

Dependencies and integration points: Included by IO, scheduler, transport, NVM MAC address parsing, debug dump, firmware load, and PCIe power-management code.

Risks: Address mistakes can access wrong internal blocks. Device-family register variants require correct selector logic outside this header. Reset/NMI doorbell bits overlap with suspend/resume/PNVM notifications on newer families. Scheduler constants must match `iwl-scd.h` helpers.

Test signals: Hardware boot/reset smoke tests, RF-kill interrupt tests, MAC address readback, firmware debug dump validation, scheduler queue setup, NMI/reset handshake on each supported family, and register dump sanity checks.
