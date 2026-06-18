<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat.service -->
# sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat.service

Purpose: this systemd unit runs `kvm_stat` as a background logger for KVM module trace events.

Important APIs/directives: `[Unit]` sets a description and orders the service before `qemu-kvm.service`. `[Service]` uses `Type=simple`, executes `/usr/bin/kvm_stat -dtcz -s 10 -L /var/log/kvm_stat.csv`, reloads with `SIGHUP`, restarts always after 60 seconds, and sets syslog identity/level. `[Install]` targets `multi-user.target`.

Control flow: systemd starts the Python tool in debugfs plus tracepoint mode, CSV mode, skip-zero-records mode, 10-second interval, and log-to-file mode. Reload sends SIGHUP, which `kvm_stat` handles by closing/reopening the log path and reprinting headers as needed.

State and persistence: persistent output is `/var/log/kvm_stat.csv`. Systemd restart policy keeps monitoring alive across failures.

Dependencies/integration: depends on installed `/usr/bin/kvm_stat`, readable debugfs/tracing/KVM state, and system permissions suitable for perf/debugfs access. Ordering before qemu-kvm means it should be available early for VM launches.

Risks and test signals: risks include missing permissions, absent debugfs, log growth, restart loops, and startup before KVM modules are loaded. Test `systemctl start/reload/status`, CSV creation, SIGHUP rotation behavior, and failure output when tracing is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/kvm/kvm_stat/kvm_stat.service -->
