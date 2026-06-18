# sources/distributed-fs/ceph-client/include/soc/at91/at91sam9_ddrsdr.h

Purpose: provides register offsets and bit definitions for Atmel AT91SAM9 DDR/SDR SDRAM controllers.

Important APIs and types: constants define mode, refresh timer, configuration, timing parameter, low-power, memory-device, DLL, high-speed, delay I/O, and write-protection registers. Bitfields cover command modes, column/row bits, CAS latency, DLL reset/disable, off-chip driver, low-power policy, partial array self-refresh, temperature compensation, data bus width, memory type, delay tuning, and write-protect status/source.

Control flow: memory initialization and power-management code programs geometry/timing registers, issues NOP/precharge/load-mode/refresh/normal commands through `MR`, configures low-power behavior, and optionally uses write-protection keys/status while touching controller registers.

State and persistence: controller state is hardware register state affecting live SDR/DDR operation. The header has no software storage; settings are re-established by boot firmware/kernel initialization.

Dependencies and integration points: standalone macro header used by AT91 memory, suspend, and platform code.

Risks and test signals: risks are incorrect timing values, wrong memory-device/width selection, malformed write-protect key use, and accidental deep power-down/self-refresh transitions. Test memory bring-up on SDR/DDR/LPDDR/DDR2 variants, suspend/resume, refresh error behavior, write-protection violation reporting, and register definitions against datasheets.
