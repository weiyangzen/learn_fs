# sources/control-plane/mayastor/test/python/v1/nexus/test_remote_only.py

Purpose: repeated smoke test for a nexus that has only remote children and no local bdev on the nexus node.

Important APIs and control flow: `ensure_zero_devices` checks bdev lists on `ms0` and `ms1`; `create_publish` creates one nexus on the local node from remote child URIs, publishes it, waits two seconds, and destroys it; `delete_all_bdevs` unshares and destroys malloc bdevs. `test_remote_only` runs ten times, creates malloc bdevs on remote `ms1`, shares them, creates/publishes/destroys the nexus on `ms0`, deletes remote bdevs, and asserts no devices remain.

State, dependencies, and integration: state is malloc bdevs, share URIs, transient nexus records, and bdev lists on two nodes. It depends on v1 module-scoped fixtures and the four-node nexus compose stack.

Risks and test signals: `ensure_zero_devices` only asserts the last iterated node’s bdev count because the assertion is outside the loop. `create_publish` destroys without unpublishing. The main signal is leak detection after repeated remote-only create/publish/destroy cycles.
