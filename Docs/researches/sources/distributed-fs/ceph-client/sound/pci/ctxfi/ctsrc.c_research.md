# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctsrc.c

## Purpose

This file implements Sample Rate Converter resource management and SRC input-mapper resource management for ctxfi.

## Important APIs, types, and functions

Public constructors/destructors are `src_mgr_create()`, `src_mgr_destroy()`, `srcimp_mgr_create()`, and `srcimp_mgr_destroy()`. SRC operations wrap hardware setters for state, format, buffer mode, pitch, addresses, and commit. `get_src_rsc()`/`put_src_rsc()` allocate and release SRC resources. SRCIMP operations include `srcimp_map()`, `srcimp_unmap()`, `get_srcimp_rsc()`, and `put_srcimp_rsc()`.

## Control flow

SRC creation initializes a generic resource manager, disables all 256 SRCs, and installs callbacks. A source request allocates one or more contiguous SRCs for interleaved memory-read mode or one SRC for write/ring modes, configures defaults, enables all conjugates, and commits manager state. Commits program the master resource and relevant conjugates. SRCIMP creation seeds the mapper list with a zero entry; mapping allocates per-MSR imapper entries and uses `ctimap` to maintain a sorted circular chain that is written to hardware through `srcimp_map_op()`.

## State and persistence behavior

SRC manager state includes bitmap allocation, manager control block, spinlock, card pointer, and global `conj_mask` derived from hardware. Each `struct src` stores mode, multi count, interleave link, and generic resource state. SRCIMP state includes allocated indexes per conjugate, mapper entries, mapped bitmask, manager pointer, and a shared mapper list protected by `imap_lock`.

## Dependencies and integration points

It depends on `ctsrc.h`, `cthardware.h`, `ctresource.c`, and `ctimap.c`. ATC and PCM preparation use SRC resources for host-memory reads/writes and audio-ring routing. Mixer/routing code consumes SRC output slots and SRCIMP mappings.

## Risks and test signals

Risks include the file-scope `conj_mask` being shared across devices, error unwinding with partially allocated SRCIMP indexes, MEMRD interleave allocation assumptions, ignored mapper callback errors, and incorrect conjugate programming for high sample-rate multiples. Tests should exercise playback/capture resource allocation at MSR 1/2/4, SRCIMP map/unmap ordering, resource exhaustion, and suspend/resume reconfiguration.
