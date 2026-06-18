# sources/distributed-fs/orangefs/src/apps/admin/module.mk.in

## Purpose
`module.mk.in` contributes the OrangeFS admin application sources to the build system. It defines the admin client program source list and the server-side admin utility source list relative to `src/apps/admin`.

## Important APIs, Types, And Functions
The file is Make input, not C code. Its important variables are `DIR`, `ADMINSRC`, and `ADMINSRC_SERVER`. `ADMINSRC` lists utilities such as debug/performance/event controls, `pvfs2-ls`, `pvfs2-stat`, `pvfs2-mkdir`, `pvfs2-chmod`, `pvfs2-chown`, `pvfs2-fs-dump`, `pvfs2-fsck`, `pvfs2-cp`, xattr/touch/link/remove tools, check/drop-cache tools, and credential tools gated by security options. `ADMINSRC_SERVER` lists server-space tools such as `pvfs2-mkspace` and `pvfs2-showcoll`.

## Control Flow
During Makefile generation/build inclusion, the variable appends add source files to the broader build's admin target lists. Conditional blocks include credential-related tools depending on `ENABLE_SECURITY_KEY` or `ENABLE_SECURITY_CERT`.

## State And Persistence
The file has no runtime state. Its persistent effect is build graph composition: changing it changes which admin programs are compiled and distributed.

## Dependencies And Integration Points
It integrates with OrangeFS's autoconf/Make infrastructure and assumes the surrounding build logic consumes `ADMINSRC` and `ADMINSRC_SERVER`. It is the build integration point for many files in this subset.

## Risks And Test Signals
Risks are omissions, stale file names, and conditional security-tool build drift. Build-system tests should verify that listed tools compile under normal, key-security, and cert-security configurations and that server-only utilities are not linked into client admin targets incorrectly.
