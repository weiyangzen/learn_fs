# sources/distributed-fs/ceph-client/fs/gfs2/trans.h

## Purpose
`trans.h` declares the GFS2 transaction API and common log credit constants used across metadata mutators.

## Important APIs And Constants
Credit constants such as `RES_DINODE`, `RES_INDIRECT`, `RES_RG_HDR`, `RES_RG_BIT`, `RES_EATTR`, `RES_STATFS`, and `RES_QUOTA` give callers shared accounting units. `gfs2_rg_blocks` returns the rgrp bitmap/header credit needed for a request, capped by the current rgrp length. Transaction APIs cover begin/end, adding data and metadata buffers, adding/removing revokes, and freeing transaction objects.

## Control Flow And State
Callers reserve credits before mutating metadata, add every changed buffer to the active transaction, and end the transaction to commit or release log reservations. `gfs2_rg_blocks` depends on `ip->i_res.rs_rgd`, so it is only valid after in-place reservation has selected a resource group.

## Dependencies And Integration Points
The header depends on buffer heads and GFS2 in-core transaction, rgrp, inode, glock, and bufdata types. It is included by rgrp, xattr, superblock, inode, quota, and directory code.

## Risks And Test Signals
The central risk is under-reserving log credits, which may trigger transaction assertions or forced withdraws. Compile coverage catches signature drift; runtime coverage comes from metadata-heavy tests, xattr allocation/deallocation, rgrp allocation, quota updates, and crash replay.
