# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-g2d/g2d-regs.h

Purpose: register and constant definitions for the Samsung G2D BitBLT engine.

Important constants: defines general, command, rotate/direct, source, destination, pattern, mask, clip, ROP/alpha, color, and color-key register offsets. It also defines pixel color mode encodings via `COLOR_MODE(order, mode)`, common ROP4 values (`ROP4_COPY`, `ROP4_INVERT`), hardware limits (`MAX_WIDTH`, `MAX_HEIGHT`), defaults, timeout, scaling defaults, and v3 stretch command bit.

Control flow role: consumed by `g2d-hw.c` to translate `g2d_frame` and control state into MMIO writes, and by `g2d.c` for format hardware values and validation limits.

State and persistence: no runtime state; describes volatile hardware register layout and supported value encodings.

Dependencies and integration: standalone header used inside the G2D driver. Its limits feed V4L2 format validation, while mode macros feed the `formats[]` table in `g2d.c`.

Risks: hardware limit constants and mode encodings must match SoC revision behavior. The 12-bit coordinate writes in the helper layer make it important that these limits and validation stay in sync.

Test signals: compile tests, format enumeration/try_fmt validation, and hardware smoke tests for every listed RGB format and ROP value.
