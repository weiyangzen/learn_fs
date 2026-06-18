# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mad.c

## Purpose
`mad.c` implements mlx5 RDMA MAD handling and MAD_IFC query helpers. It filters incoming management datagrams, forwards supported classes/methods to firmware, provides special PMA counter handling, and exposes helper queries for node, port, P_Key, and GID data used by `main.c`.

## Important APIs, Types, And Functions
The central entry point is `mlx5_ib_process_mad()`. Query helpers include `mlx5_query_ext_port_caps()`, `mlx5_query_mad_ifc_system_image_guid()`, `mlx5_query_mad_ifc_max_pkeys()`, `mlx5_query_mad_ifc_vendor_id()`, `mlx5_query_mad_ifc_node_desc()`, `mlx5_query_mad_ifc_node_guid()`, `mlx5_query_mad_ifc_pkey()`, `mlx5_query_mad_ifc_gids()`, and `mlx5_query_mad_ifc_port()`. Internal helpers include `mlx5_MAD_IFC()`, `process_pma_cmd()`, `query_ib_ppcnt()`, and PMA assignment routines for standard and extended counters.

## Control Flow
`mlx5_ib_process_mad()` ignores unsupported management classes and methods, consumes invalid trap requests, handles PMA GETs locally when vport counters are supported, and otherwise calls `mlx5_MAD_IFC()`. `mlx5_MAD_IFC()` checks SMI permission for subnet management classes using `dev->port_caps[].has_smi`, builds an operation modifier for ignored M_Key/B_Key checks, and calls `mlx5_cmd_mad_ifc()`.

PMA handling determines the native mlx5 port for the RDMA port, falls back to the PF first port when a multiport peer is unaffiliated, and uses PPCNT registers for SMI devices or vport counters for normal devices. `IB_PMA_CLASS_PORT_INFO` replies advertise extended-width counters. Port query helpers construct SMPs, issue MAD_IFC queries, and decode fixed byte offsets into RDMA core structures, including extended speed handling for FDR/EDR/HDR/NDR/XDR and FDR-10 extended-port info.

## State And Persistence Behavior
The file does not own long-lived mutable state. It reads `dev->port_caps` and may set `ext_port_cap` in `mlx5_query_ext_port_caps()`. All MAD buffers and register outputs are per-call allocations. Firmware and hardware counters are queried on demand.

## Dependencies And Integration Points
`main.c` installs `mlx5_ib_process_mad()` in `ib_device_ops` and uses the query helpers for MAD-backed access on IB ports without virtualized HCA access. The file depends on RDMA MAD/SMP/PMA definitions, mlx5 command MAD_IFC support from `cmd.h`, mlx5 PPCNT register access, and multiport native-port resolution functions from `main.c`.

## Risks
MAD data decoding uses fixed offsets into SMP data; spec or firmware layout mismatches would produce wrong attributes. PMA paths allocate buffers sized for the max of vport-counter and PPCNT structures; size mistakes can corrupt decoding. SMI permission depends on earlier `set_has_smi_cap()` initialization. Native-port fallback for unaffiliated multiport devices intentionally returns data for port 1, which can be surprising during hotplug or partial initialization.

## Test Signals
Exercise MAD GET/SET/TRAP_REPRESS filtering, SMI permission denial, PMA standard and extended counter queries on SMI and non-SMI devices, port attribute decoding across IB link speeds, P_Key and GID table queries, and multiport unaffiliated fallback behavior.
