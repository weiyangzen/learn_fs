# sources/cloud-native/ostree/src/boot/ostree-tmpfiles.conf

Purpose: This tmpfiles configuration creates OSTree runtime directories and removes stale temporary unlock overlay directories.

Important APIs, types, and functions: It declares `d /run/ostree 0755 root root -` and `R! /var/tmp/ostree-unlock-ovl.*`.

Control flow: systemd-tmpfiles processes the rules during tmpfiles setup. Directory creation and removal are declarative.

State and persistence behavior: Ensures `/run/ostree` exists for runtime state and force-removes matching `/var/tmp/ostree-unlock-ovl.*` paths at tmpfiles cleanup time. `/run` state is volatile; `/var/tmp` cleanup affects persistent temporary state.

Dependencies and integration points: Used by systemd-tmpfiles and comments reference historical unlock overlay behavior. It complements boot services that use `/run/ostree`.

Risks: The removal glob must stay specific; overly broad cleanup could delete unrelated data. Removing stale overlay temp dirs is useful, but active use must not overlap tmpfiles cleanup timing.

Test signals: Validation comes from tmpfiles runs and checking runtime directory presence/cleanup behavior.
