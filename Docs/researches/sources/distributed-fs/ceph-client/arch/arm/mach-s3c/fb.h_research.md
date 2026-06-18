# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/fb.h

Purpose: Samsung framebuffer platform-data helper declarations.

Important APIs/types/functions: declares `s3c_fb_set_platdata()` and framebuffer-related platform-data types used by legacy board setup.

Control flow: no local flow.

State and persistence: platform data configured through these declarations affects static framebuffer device state.

Dependencies and integration points: used by `devs.c`, board files, and the S3C framebuffer driver.

Risks: mismatched platform data can break display timing, DMA, or panel setup.

Test signals: framebuffer probe and panel mode operation on legacy boards.
