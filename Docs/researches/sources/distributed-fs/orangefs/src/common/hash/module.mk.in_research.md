# sources/distributed-fs/orangefs/src/common/hash/module.mk.in

Purpose: Build-fragment registration for the MurmurHash3 implementation.

Important build variables: Sets `DIR := src/common/hash`, then appends `murmur3.c` to `SERVERSRC` and `LIBSRC`.

Control flow/state: Make fragment only.

Dependencies/integration: Makes MurmurHash3 available to server and common library consumers, but not explicitly to BMI.

Risks: If BMI code needs Murmur3, this fragment will not include it in `LIBBMISRC`. There are no per-file flags for endian/alignment portability.

Test signals: Link targets that call `MurmurHash3_*` from library/server code and compare known hash vectors.
