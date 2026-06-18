# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/multi-user.target.wants/notify-multiuser.service

Purpose: enables the `notify-multiuser.service` workaround by placing the unit in `multi-user.target.wants`.

Important APIs/types/functions: unit content matches `notify-multiuser.service`: `After/Wants=multi-user.target`, `LoadCredential=vmm.notify_socket`, `ExecStart=/etc/notify-multiuser.py`, `Type=exec`, `RemainAfterExit=yes`.

Control flow: systemd treats this path as an enablement symlink/copy and starts the notifier after multi-user target.

State/persistence: persistent unit enablement in the workaround tree.

Dependencies/integration: depends on systemd unit loading and the Python notifier script.

Risks/test signals: duplicated full unit instead of symlink can drift from the canonical service file. VM harness readiness depends on it.
