# sources/distributed-fs/ceph-client/arch/sh/mm/consistent.c

Purpose: manages command-line and platform setup for consistent DMA memory chunks.

Important functions: `memchunk_setup`, `memchunk_cmdline_override`, and `platform_resource_setup_memory`.

Control flow: early command-line parsing can override memory chunk placement/size. Platform setup installs memory resources for devices using the configured coherent memory range.

State and persistence: stores command-line-derived physical memory chunk configuration and platform resource descriptors for runtime device probing.

Dependencies and integration: depends on platform devices, DMA mapping, memory/init infrastructure, and I/O resource registration.

Risks: incorrect chunk reservation can overlap RAM or starve DMA-capable devices. Command-line parsing must validate physical ranges.

Test signals: boot with memchunk parameters, platform resource inspection, and DMA allocation behavior on devices requiring consistent memory.
