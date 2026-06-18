# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.h

## Purpose
Declares the libgfchangelog RPC surface for probe-client setup, probe invocation, and reverse listener setup.

## APIs, Types, and Functions
Exports `gf_changelog_rpc_init(xlator_t *, gf_changelog_t *)`, `gf_changelog_invoke_rpc(xlator_t *, gf_changelog_t *, int)`, and `gf_changelog_reborp_init_rpc_listner(xlator_t *, char *, char *, void *)`. It includes libgfchangelog helper definitions and shared changelog RPC constants/functions.

## Control Flow, State, and Persistence
The header has no runtime state. It describes the two-channel registration flow: create a reverse RPC listener, initialize a forward RPC client to the brick changelog socket, then invoke a probe procedure that asks the brick to connect back.

## Dependencies and Integration
Included by `gf-changelog.c`, `gf-changelog-rpc.c`, and other library files needing RPC setup. It bridges library-side helper types with xlator-side `changelog-rpc-common.h`.

## Risks and Test Signals
Risks are API typo compatibility (`listner` spelling), incomplete ownership documentation for socket buffers and callback data, and tight coupling to common RPC program constants. Test signals are compile coverage of all declarations and registration flows using both legacy journal callbacks and generic callbacks.
