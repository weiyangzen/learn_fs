# sources/cloud-native/ostree/src/boot/ostree-boot-complete.service

Purpose: This systemd oneshot marks an OSTree boot as complete and handles cleanup/failure propagation before staged deployment finalization.

Important APIs, types, and functions: Unit conditions require `ostree` on the kernel command line and either `/boot/ostree/finalize-failure.stamp` or `/run/ostree/nextroot-booted`. It has `DefaultDependencies=no`, runs `After=sysinit.target`, requires mounts for `/boot`, and runs `Before=ostree-finalize-staged.service`. Service uses `MountFlags=slave`, `RemainAfterExit=yes`, and `ExecStart=/usr/bin/ostree admin boot-complete`.

Control flow: systemd starts it early when conditions match. The OSTree CLI performs the actual boot-complete logic and any soft-reboot cleanup.

State and persistence behavior: The service may write to `/boot` through the OSTree command, including removing or recording boot/finalization state. It remains active after completion to preserve ordering.

Dependencies and integration points: Integrates with staged deployment finalization, boot-complete CLI implementation, `/boot` mount availability, and soft reboot state under `/run/ostree`.

Risks: If it fails or is skipped incorrectly, finalization failure markers may not propagate and later staged finalization can run with stale state. `/boot` mount accessibility and namespace behavior are important.

Test signals: No direct test here; systemd boot integration and OSTree admin command tests provide validation.
