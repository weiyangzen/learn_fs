# sources/distributed-fs/ceph-client/arch/mips/include/asm/video.h

## Purpose

`video.h` provides framebuffer pgprot and 64-bit raw framebuffer read/write helpers before including generic video helpers.

## Important APIs, Types, And Functions

The concrete API surface is listed below from the header declarations and macros. Includes: `asm/page.h`, `asm-generic/video.h`. Macros/constants: `_ASM_VIDEO_H_`, `pgprot_framebuffer`, `fb_readq`, `fb_writeq`. Functions/prototypes/helpers: `fb_writeq`, `pgprot_noncached`, `__raw_readq`, `__raw_writeq`.

## Control Flow

Control flow is mostly implemented at call sites; this header supplies inline helpers, constants, prototypes, or type layouts that guide architecture setup and runtime low-level paths.

## State And Persistence

State depends on the subsystem: CPU topology masks, exception vectors, module metadata, VPE lists, hardware watch registers, write buffers, VGA memory, framebuffer mappings, or boot-time FDT contents.

## Dependencies And Integration Points

It integrates with framebuffer mmap and IO helpers.

## Risks

Risks are low-level build failures, ABI/layout drift, wrong hardware constants, or stale hooks that only fail on specific MIPS boards/CPU features.

## Test Signals

Test signals are MIPS defconfig/allmodconfig builds, subsystem-specific boot coverage, and targeted runtime tests for the exposed hardware path.
Static review signal: this source currently has 39 lines and 875 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
