# sources/distributed-fs/ceph-client/arch/parisc/video/video-sti.c

## Purpose
PA-RISC helper that decides whether a framebuffer device is the primary display when STI firmware graphics are present.

## Important APIs, Types, And Control Flow
`video_is_primary_device(struct device *dev)` is exported for framebuffer/video drivers. It calls `sti_get_rom(0)` to find the default built-in STI graphics device. If no STI ROM exists, it returns true so any framebuffer can become default. If STI exists, it returns true only when `sti->dev == dev`.

## State, Dependencies, Risks, And Tests
The function does not persist state; it reads STI core global/device discovery state. Dependencies include `<video/sticore.h>`, `<asm/video.h>`, and module export infrastructure. Risks include NULL/default-ROM ambiguity, stale `sti->dev`, and multi-adapter systems choosing the wrong primary display. Test signals are PA-RISC boots with no STI, one built-in STI framebuffer, and additional non-primary framebuffers; also module symbol resolution for framebuffer drivers.
