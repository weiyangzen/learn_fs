# sources/distributed-fs/ceph-client/arch/sparc/video/Makefile

Purpose: builds common SPARC video helper code.

Important APIs/targets: unconditionally adds `video-common.o` to `obj-y`.

Control flow: kbuild compiles the helper into the architecture video support.

State and persistence: no runtime state in this file.

Dependencies and integration points: integrates the primary-console device helper with SPARC video/framebuffer drivers.

Risks: omitting the object prevents drivers from resolving `video_is_primary_device()`.

Test signals: SPARC builds with framebuffer/video drivers and link checks for exported video helper symbols.
