# File Research: sources/cow-pools/bcachefs-tools/fs/debug/sysfs.h

## Purpose

Declares the sysfs entry points and attribute lists implemented by `debug/sysfs.c`.

## Main Interfaces

Exports attribute arrays for filesystem, counter, internal, option, time-stat, JSON time-stat, and device directories. Exports the corresponding `struct sysfs_ops` objects, `bin_attr_btree_trans_stats_json`, and `bch2_opts_create_sysfs_files()`.

## Dependencies

Includes Linux sysfs declarations and forward-declares `struct attribute` and `struct sysfs_ops`.

## Notes

This header is purely declarative. It defines the contract consumed by bcachefs kobject setup code and keeps sysfs registration decoupled from the large implementation file.
