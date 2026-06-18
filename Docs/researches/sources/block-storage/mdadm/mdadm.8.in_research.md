# File Research: sources/block-storage/mdadm/mdadm.8.in

## Role

`mdadm.8.in` is the primary manual page source for the `mdadm` command. It documents supported RAID concepts, command modes, options, operational workflows, environment variables, examples, device naming, and related files.

## Major Content Areas

- Defines mdadm as the tool for managing Linux md Software RAID devices.
- Describes supported personalities: Linear, RAID0/1/4/5/6/10, multipath, faulty, and container.
- Explains container metadata, especially DDF and IMSM, where one metadata set manages multiple member arrays.
- Documents modes: Assemble, Build, Create, Follow/Monitor, Grow, Incremental Assembly, Manage, Misc, and Auto-detect.
- Documents global options such as help, version, verbosity, force, config, scan, metadata, homehost, prefer, and home-cluster.
- Documents create/build/grow geometry and consistency options: raid devices, spares, size, array-size, chunk, level, layout, bitmap, write-mostly, write-behind, failfast, assume-clean, write-zeroes, backup-file, data-offset, name, nodes, write-journal, consistency-policy, and logical-block-size.
- Documents assemble-specific identity and recovery options: uuid, super-minor, name, force, run, no-degraded, backup-file, invalid-backup, and update options.
- Documents manage mode operations: add, re-add, add-spare, remove, fail, replace/with, cluster-confirm, add-journal, write-mostly/readwrite, failfast/nofailfast, and test.
- Documents misc operations: query, detail, detail-platform, export, examine, bitmap/badblocks examination, dump/restore, run/stop, readonly/readwrite, zero-superblock, kill/update-subarray, wait/wait-clean, action, and udev-rules.
- Documents incremental and monitor modes in detail.
- Explains grow-mode size, raid-device, level, chunk/layout, bitmap, and consistency-policy changes.
- Lists environment variables: `MDADM_NO_MDMON`, `MDADM_NO_UDEV`, `MDADM_NO_SYSTEMCTL`, `IMSM_NO_PLATFORM`, `MDADM_GROW_ALLOW_OLD`, and `MDADM_CONF_AUTO`.
- Provides examples, file references, POSIX portable name rules, device naming rules, output interpretation, and related links/manpages.

## Integration With Code

This manual corresponds closely to option parsing in `mdadm.c` and mapping definitions in `maps.c`. Placeholder tokens such as `{DEFAULT_METADATA}`, `{CONFFILE}`, `{CONFFILE2}`, and `{MAP_PATH}` are substituted at build/install time. The documented update options match `update_options[]`, documented modes match `modes[]`, and layout/policy names match mapping tables.

## Important Operational Semantics

- Auto-assembly uses config, homehost, metadata type policy, and device discovery to choose names and whether arrays are local or foreign.
- Grow operations can be destructive or non-reversible; the manual emphasizes filesystem resizing, array-size staging, and backup-file requirements.
- Backup files are required for several reshape cases and must be supplied on assemble after crashes.
- Monitor mode can send mail, run alert programs, log to syslog, move spares by spare-group or policy domain, and integrates with systemd mdmonitor service.
- Incremental mode is designed for hotplug/udev, maintains `{MAP_PATH}`, and can start arrays when enough devices arrive or later via `--incremental --run --scan`.
- Device names can be kernel-style numeric md names or chosen `/dev/md/` names, with suffixes added for conflicts or foreign arrays.

## Risks and Documentation Invariants

- This file is the user-facing contract. Parser behavior, accepted option values, and mode constraints in `mdadm.c` should remain synchronized with it.
- The grow and force sections document high-risk operations where inaccurate wording could lead to data loss.
- Deprecated features such as md/multipath, faulty, DDF, kernel auto-detect, and `--auto` need documentation consistency with code warnings and compatibility behavior.
