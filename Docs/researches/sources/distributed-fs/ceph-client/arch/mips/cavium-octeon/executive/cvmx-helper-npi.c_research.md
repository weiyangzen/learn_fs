# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-npi.c

## Purpose
Supports the PCI/host-facing NPI packet interface by detecting supported ports and applying minimal PIP configuration.

## Important APIs, Types, And Functions
Entry points are `__cvmx_helper_npi_probe()` and `__cvmx_helper_npi_enable()`. The code uses `CVMX_PKO_QUEUES_PER_PORT_PCI`, model/pass checks, helper port counts, and `CVMX_PIP_PRT_CFGX`.

## Control Flow
Probe returns four ports only on models/pass levels with packet engines and PCI queues configured. Enable disables min/max length checks on applicable chips and leaves actual enable control to the remote host.

## State, Persistence, And Dependencies
State is PIP port CSR configuration. Existence depends on compile-time queue configuration and chip model.

## Integration Points
The generic helper treats NPI as a packet I/O interface for IPD/PKO setup but not as an Ethernet link-status interface.

## Risks
Wrong model gating can expose nonexistent engines. Local enable success does not prove the remote host has enabled traffic.

## Test Signals
Check probe counts on supported and unsupported models, host-driven packet movement, and absence of false length errors.
