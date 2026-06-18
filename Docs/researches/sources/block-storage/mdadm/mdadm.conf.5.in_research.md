# File Research: sources/block-storage/mdadm/mdadm.conf.5.in

## Role

`mdadm.conf.5.in` is the manual page source for mdadm’s configuration file. It defines file syntax, supported directives, auto-assembly policy, alert settings, creation defaults, hotplug policy, sysfs defaults, monitoring delay, encryption verification overrides, probing options, default config file locations, and examples.

## Syntax Rules

- The file is parsed as whitespace-separated words.
- `#` starts a comment from that word to end of line.
- Single or double quotes protect whitespace.
- Lines beginning with whitespace continue the previous line.
- Empty lines are ignored.
- Keywords are case-insensitive and can generally be abbreviated to three characters, with noted exceptions.

## Directives

- `DEVICE`: lists devices/patterns to scan, or special words `containers` and `partitions`. Defaults to `DEVICE partitions containers` when absent.
- `ARRAY`: identifies arrays by device name or `<ignore>`, then identity tags such as `uuid=`, `super-minor=`, `devices=`, `level=`, `num-devices=`, `spares=`, `spare-group=`, `bitmap=`, `metadata=`, `container=`, and `member=`.
- `MAILADDR`: email recipient for monitor alerts.
- `MAILFROM`: configured sender address for alert email.
- `PROGRAM`: external program run for monitor events.
- `CREATE`: defaults for owner, group, mode, metadata, names, and bad-block-list behavior.
- `HOMEHOST`: default homehost policy, including `<system>`, `<none>`, and `<ignore>`.
- `HOMECLUSTER`: default md cluster name.
- `AUTO`: metadata/homehost auto-assembly allow/deny policy.
- `POLICY`: hotplug and spare migration policy by domain, metadata, path, type, action, and auto.
- `PART-POLICY`: partition-oriented form of policy with per-partition domain derivation.
- `SYSFS`: sysfs attribute defaults applied after assembly by uuid or name, in reverse order.
- `MONITORDELAY`: default monitor polling delay.
- `ENCRYPTION_NO_VERIFY`: disables selected encryption verification, currently `sata_opal` for IMSM contexts.
- `PROBING`: probe behavior options such as extended DDF header scanning.

## Policy Semantics

`POLICY` and `PART-POLICY` describe what mdadm may do automatically for newly appearing devices. Actions are ordered by permissiveness: include, re-add, spare, spare-same-slot, and force-spare. Domains allow spare migration when destination domains contain the new disk’s domains or arrays share a spare group.

## Files Documented

The manual documents primary and alternative config files plus their `.d` directories. Directory files are read in lexical order. Placeholder tokens such as `{CONFFILE}` and `{CONFFILE2}` are substituted during build.

## Integration With Code

The directives documented here are consumed by mdadm config parsing and used by `mdadm.c`, `mapfile.c`, incremental assembly, monitor spare migration, udev rule generation, create defaults, and sysfs post-assembly configuration.

## Important Invariants

- Only one effective `MAILADDR`, `PROGRAM`, `AUTO`, `HOMECLUSTER`, and first non-zero monitor delay are expected according to documentation.
- Later `CREATE` lines override earlier settings.
- `ARRAY <ignore>` prevents automatic assembly of matching arrays.
- AUTO policy is first-match-wins.
- Policy line ordering does not affect the final most-permissive action.

## Risks

Configuration behavior affects unattended boot, hotplug, spare migration, and alerting. Documentation must stay synchronized with parser keyword names and policy implementation, especially for automatic actions that can add bare disks or migrate spares.
