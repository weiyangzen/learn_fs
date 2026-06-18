# sources/cloud-native/ostree/src/boot/ostree-state-overlay@.service

Purpose: This templated systemd unit creates an OSTree state overlay on a selected top-level path such as `/%I`.

Important APIs, types, and functions: It runs only on OSTree boots, has no default dependencies, runs after `var.mount` and `boot.mount`, before `local-fs.target`, and executes `/usr/bin/ostree admin state-overlay %i /%I`. It remains active and is wanted by `local-fs.target`.

Control flow: For each enabled instance, systemd substitutes the instance name into `%i` and `%I`, waits for `/var` and `/boot`, then invokes the OSTree CLI before local filesystems are considered ready.

State and persistence behavior: The CLI stores upperdir state under `/var` and overlays the requested path. This affects runtime writable state for otherwise immutable deployments.

Dependencies and integration points: Integrates with OSTree admin CLI, systemd template units, `/var` storage, boot/sysroot metadata, and local-fs ordering.

Risks: Instance naming controls the target path, so misconfiguration can overlay the wrong directory. Overlay setup before local-fs is timing-sensitive and depends on `/var` availability.

Test signals: No direct tests here; validation requires enabled unit instances and boot-time overlay behavior checks.
