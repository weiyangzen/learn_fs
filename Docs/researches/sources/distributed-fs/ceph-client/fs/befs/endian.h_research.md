# sources/distributed-fs/ceph-client/fs/befs/endian.h

Purpose: centralizes BeFS filesystem-endian conversion for scalar and composite on-disk fields.

Important APIs/types/functions: `fs64_to_cpu`, `cpu_to_fs64`, `fs32_to_cpu`, `cpu_to_fs32`, `fs16_to_cpu`, `cpu_to_fs16`, `fsrun_to_cpu`, `cpu_to_fsrun`, and `fsds_to_cpu`.

Control flow: conversion branches on `BEFS_SB(sb)->byte_order`, which is set while loading the superblock. Composite helpers convert block runs and full datastreams into host-endian forms.

State and persistence: no state, but correctness depends on persistent superblock byte-order detection.

Dependencies and integration: used by all BeFS disk parsing and debug dumping code; includes architecture byteorder helpers.

Risks: using conversion before `byte_order` is initialized or mixing host/disk structures can corrupt addressing. Sparse bitwise fs types help catch misuse.

Test signals: mount little- and big-endian BeFS images; sparse endian checks; compare debug dumps against known disk metadata.
