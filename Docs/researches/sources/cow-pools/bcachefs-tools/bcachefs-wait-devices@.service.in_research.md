# File Research: sources/cow-pools/bcachefs-tools/bcachefs-wait-devices@.service.in

- systemd oneshot template service for waiting on all devices in a bcachefs filesystem UUID.
- `@sbindir@` is substituted by the Makefile.
- Runs `bcachefs wait-devices UUID=%i` and remains active after success.
