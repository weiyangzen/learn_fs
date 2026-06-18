# sources/cloud-native/ostree/tests/test-demo-buildsystem.sh

Purpose: demonstrates and tests an OSTree-based package compose workflow using package commits, union checkouts, triggers, publish, deltas, and summaries.

Important APIs/functions: `skip_without_fuse`, `skip_without_user_xattrs`, functions `demo_triggers()`, `exampleos_build_commit_package()`, and `exampleos_recompose()`, plus `rofiles-fuse`, `fusermount -u`, `commit --link-checkout-speedup`, `pull-local`, `static-delta generate`, and `summary -u`.

Control flow: initializes a bare-user build repo and archive publish repo, builds fake `bash` and `systemd` package refs, recomposes by union checkout and trigger execution through a rofiles-fuse mount, publishes the standard ref, updates one package, recomposes, republishes, generates a delta, and updates the summary.

State/persistence: writes build-package directories, `exampleos-build`, FUSE mount `mnt`, build and publish repos, deltas, and summaries. Dependencies include FUSE and user xattrs.

Integration/risk/test signals: validates a realistic build-system pattern and link-checkout optimization. Risks are FUSE availability and date-varying trigger output. One TAP case reports the demo workflow.
