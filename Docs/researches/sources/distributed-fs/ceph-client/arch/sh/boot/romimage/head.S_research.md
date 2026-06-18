# sources/distributed-fs/ceph-client/arch/sh/boot/romimage/head.S



Source read size: 85 lines, 1637 bytes.



Purpose: ROM-image entry trampoline that performs board-specific setup, optionally loads the image from MMCIF, copies the zero page to the kernel's expected location, and jumps to zImage.

Important APIs/types/functions: global `romstart`, included `mach/romimage.h`, optional `mmcif_loader`, labels `loaded_code`, `empty_zero_page_dst`, `extra_data_pos`, and `zero_page_pos` from the linked payload.

Control flow: run board setup, optionally call the MMCIF loader with destination above the zero page and jump into the loaded code, copy one page of zero-page data in 16-byte chunks to `_text`, then branch to the zImage positioned after the zero-page payload.

State and persistence: manipulates early registers, stack pointer during MMCIF load, and the in-memory zero page; no runtime state persists after kernel entry.

Dependencies and integration points: coupled to `romimage/Makefile`, `mach/romimage.h`, page constants, and optional SH7724 MMCIF loader.

Risks and test signals: payload offset math and zero-page copy order are boot-critical. Test ROM boot with and without MMCIF, verify zero-page contents, and check board-specific setup code paths.
