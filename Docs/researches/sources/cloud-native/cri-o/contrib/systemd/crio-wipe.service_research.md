# sources/cloud-native/cri-o/contrib/systemd/crio-wipe.service

## Purpose
Systemd oneshot unit that invokes crio wipe during boot to clean stale runtime/container state before CRI-O starts.

## Important APIs, Types, and Functions
Unit has DefaultDependencies=false, Before=crio.service, Wants=local-fs.target, After=local-fs.target, ConditionPathExists=!/etc/crio/crio.conf, ExecStart=/usr/local/bin/crio wipe.

## Control Flow
When enabled, systemd runs the oneshot before crio.service if condition passes, then remains after exit due to RemainAfterExit=yes.

## State and Persistence
Mutates CRI-O storage/runtime state through crio wipe; systemd unit state remains active after completion.

## Dependencies
Depends on /usr/local/bin/crio and local filesystems; condition references /etc/crio/crio.conf.

## Integration Points
Pairs with crio.service ordering so cleanup occurs before daemon start.

## Risks and Edge Cases
ConditionPathExists negation means wipe may be skipped when config exists; wipe is destructive by design; failures can block dependent startup depending systemd behavior.

## Test Signals
Operational signal is systemctl status/journal for crio-wipe and subsequent CRI-O clean start.
