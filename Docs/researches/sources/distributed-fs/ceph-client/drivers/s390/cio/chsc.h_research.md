# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc.h

## Purpose
This header declares CHSC request/response layouts, channel-measurement descriptor formats, CSS characteristic structures, SCM information structures, and the public CHSC helper API used throughout s390 common I/O.

## Important APIs, Types, and Functions
Important types include `struct cmg_chars`, `struct cmg_cmcb`, `struct cmg_entry`, `struct cmg_ext_entry`, `struct channel_path_desc_fmt1`, `struct channel_path_desc_fmt3`, `struct css_chsc_char`, `struct chsc_ssd_info`, `struct chsc_ssqd_area`, `struct chsc_scssc_area`, `struct chsc_scpd`, `struct chsc_sda_area`, `struct sale`, and `struct chsc_scm_info`. It declares CHSC helpers for SSD, CSS characteristics, facility enable, channel-path vary/descriptions, measurement characteristics, SSQD/SADC/SGIB/SIOSL/SCM/PNSO, SCUD, and CSSID/IID lookup.

## Control Flow
The header has no executable logic except SCM stubs compiled when `CONFIG_SCM_BUS` is absent. It defines the packed ABI blocks that implementation functions fill before issuing CHSC instructions, and the declarations that let device, CSS, CMF, QDIO, SCM, and PCI code call into `chsc.c`.

## State and Persistence
The header declares exported `css_chsc_characteristics` and the external CHSC state contracts, but it does not allocate state. CHSC request areas are transient and page-aligned by callers. No persistence is defined.

## Dependencies and Integration Points
It depends on Linux types/device declarations and architecture headers for CSS characteristics, CHPID, CHSC, SCHID, and QDIO layouts. Its packed structures are hardware ABI integration points, so alignment and bitfield layout are part of the contract.

## Risks and Test Signals
Risk areas include bitfield packing drift across compilers/architecture headers, ABI-sized structure changes, feature-bit misinterpretation, and missing stubs for optional SCM users. Test signals include compile-time size/alignment checks where available, boot-time CHSC characteristic detection, QDIO/SADC and SCM callers, and cross-file builds that include `chsc.h` without extra hidden dependencies.
