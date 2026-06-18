# sources/cloud-native/ostree/src/boot/ostree-finalize-staged-hold.service

Purpose: This systemd service keeps `/boot` open for the duration of staged deployment finalization to avoid automount timeouts and namespace issues.

Important APIs, types, and functions: It requires `/run/ostree-booted`, has no default dependencies, requires mounts for `/sysroot` and `/boot`, runs after `local-fs.target`, before `basic.target` and `final.target`, and executes `+/usr/bin/ostree admin finalize-staged --hold` with `Type=exec`.

Control flow: `ostree-finalize-staged.service` wants and orders after this hold service, ensuring the hold process is active before finalization later occurs.

State and persistence behavior: The command's purpose is to keep resources open, primarily `/boot`; it is not the final mutation step itself. The `+` prefix runs with elevated/root namespace behavior.

Dependencies and integration points: Tightly paired with `ostree-finalize-staged.service`, systemd mount handling, autofs behavior, and OSTree staged deployment state.

Risks: If the hold service exits too early or cannot access `/boot`, staged finalization may fail on systems with automounted `/boot`. Root namespace execution is deliberate and security-sensitive.

Test signals: Validation is boot/shutdown integration; no direct unit tests in this subset.
