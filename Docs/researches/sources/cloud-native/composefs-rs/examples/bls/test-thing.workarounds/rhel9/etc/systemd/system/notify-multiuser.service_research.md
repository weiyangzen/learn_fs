# sources/cloud-native/composefs-rs/examples/bls/test-thing.workarounds/rhel9/etc/systemd/system/notify-multiuser.service

Purpose: systemd unit that runs the RHEL9 host-notification script at multi-user target.

Important APIs/types/functions: `LoadCredential=vmm.notify_socket`, `ExecStart=/etc/notify-multiuser.py`, `Type=exec`, and `RemainAfterExit=yes`.

Control flow: after/wants multi-user target, starts the script once and remains active.

State/persistence: persistent service definition in the guest image workaround tree.

Dependencies/integration: depends on systemd credentials and `notify-multiuser.py`; integrates with `testthing` startup readiness.

Risks/test signals: if credentials are unavailable or service ordering changes, tests wait for SSH readiness incorrectly.
