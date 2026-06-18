<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.c

## Purpose

Provides rdmavt MAD agent setup/teardown and a default MAD processing stub.

## Important APIs, Types, And Functions

`rvt_process_mad()` currently returns `IB_MAD_RESULT_FAILURE` because MAD handling is driver-specific. `rvt_create_mad_agents()` registers SMI MAD send agents for each port. `rvt_free_mad_agents()` unregisters agents and destroys stored subnet-manager AHs. `rvt_send_mad_handler()` frees completed send MAD buffers.

## Control Flow

Create loops over all ports, registers an `IB_QPT_SMI` MAD agent, stores it in `rvp->send_agent`, and optionally notifies the driver. On failure it unregisters any agents already created and sends free notifications. Teardown unregisters all agents, destroys `sm_ah`, and calls optional driver free notifications.

## State And Persistence Behavior

Per-port state includes `send_agent` and optional `sm_ah`. These persist while the rdmavt device is active.

## Dependencies And Integration Points

Depends on RDMA MAD core, rdmavt port/device structs, and driver callbacks for MAD agent lifecycle.

## Risks And Edge Cases

Default `rvt_process_mad()` is not functional; drivers that require MAD handling must override or provide their own processing. Failure unwind calls notifications only for agents that were created. Teardown must handle partially initialized ports.

## Test Signals

Test per-port agent registration, failure unwind, send completion freeing, free path destroying `sm_ah`, callback invocation, and driver-provided MAD processing paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mad.c -->
