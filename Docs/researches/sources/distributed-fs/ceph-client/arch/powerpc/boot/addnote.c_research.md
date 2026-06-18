# sources/distributed-fs/ceph-client/arch/powerpc/boot/addnote.c

## Purpose
Host utility that patches an ELF zImage with CHRP and IBM RPA `PT_NOTE` program headers so Open Firmware on RS/6000-style systems loads it correctly.

## Important APIs, Types, And Control Flow
`main()` opens an ELF file read/write, reads the first 1024 bytes, detects ELF class and endianness, validates program-header layout, checks no `PT_NOTE` already exists, finds zero-filled space after existing headers, writes two new program headers, writes the PowerPC CHRP note and RPA client-config note, increments `e_phnum`, then writes the buffer back. The macros `GET_*` and `PUT_*` abstract ELF32/ELF64 and big/little endian fields.

## State, Dependencies, Risks, And Tests
It mutates the target ELF file in place and assumes all required header/note space is within the initial 1024-byte buffer. Dependencies are POSIX file APIs and ELF layout constants encoded locally. Risks include insufficient zero padding, a likely footgun around the first/second note file-size fields, only partially validating program headers, and host-endian mistakes in note descriptors that are intentionally big-endian. Test with ELF32/ELF64, BE/LE images, images already containing `PT_NOTE`, images without slack space, and `readelf -l -n` validation after patching.
