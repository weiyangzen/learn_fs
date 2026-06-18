# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/board.h

Purpose: centralizes SiByte board header selection and exposes the LED helper contract used by assembly and C code during early boot and diagnostics.

Important APIs/types/functions: for C callers it declares `void swarm_setup(void);` and either `extern void setleds(char *str);` or a no-op `setleds(s)` macro depending on whether the selected board defines `LEDS_PHYS`. For assembler it defines a `setleds(t0, t1, c0, c1, c2, c3)` macro that writes four bytes to LED offsets from the uncached LED physical address.

Control flow: preprocessor selection includes `swarm.h`, `sentosa.h`, or `bigsur.h` based on `CONFIG_SIBYTE_*` options. The LED helper becomes active only when the included board header supplies `LEDS_PHYS`; otherwise both assembly and C LED calls compile away.

State and persistence: no ordinary software state is stored. Active LED operations write board hardware registers and persist visually until overwritten or reset.

Dependencies and integration: depends on board-specific headers for constants. It is used by early boot assembly, board setup, and platform diagnostics that need common names while still allowing board-specific resource maps.

Risks and test signals: configuration overlap can include multiple board headers if Kconfig is inconsistent, which could collide on board constants. The assembly LED macro assumes scratch registers and specific byte offsets. Test signals include all supported SiByte board defconfig builds, assembly preprocessing, boot logs that call `swarm_setup`, and visible/no-op LED behavior depending on board support.
