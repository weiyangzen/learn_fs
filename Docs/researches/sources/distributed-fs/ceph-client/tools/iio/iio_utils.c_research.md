# sources/distributed-fs/ceph-client/tools/iio/iio_utils.c

## Purpose

`iio_utils.c` provides shared sysfs utilities for the IIO example tools. It discovers IIO devices and triggers, reads channel metadata, builds sorted channel arrays, and reads/writes typed sysfs attributes.

## Important APIs and Functions

The exported `iio_dir` points to `/sys/bus/iio/devices/`. `iioutils_break_up_name` strips direction prefixes and digits to derive a generic channel name. `iioutils_get_type` parses scan element type strings like endian/sign/bits/storage/shift into channel layout fields. `iioutils_get_param_float` reads per-channel scale and offset, trying specific and generic names. `build_channel_array` scans `bufferN/*_en`, counts enabled channels, allocates `struct iio_channel_info` entries, reads indexes, scale, offset, and type data, then sorts by index. `find_type_by_name` searches IIO top-level entries for a matching `name` file. The read/write helpers handle integer, float, and string sysfs access with optional verification.

## Control Flow and State

The file has no durable state beyond sysfs mutations done by write helpers. Most functions allocate temporary path strings with `asprintf` or `malloc`, open directories and files, return negative errno-style errors, and clean up on failure. `build_channel_array` is the central state-construction path used by buffered readers: it produces an owned array whose strings must be freed by the caller.

## Dependencies and Integration

The utilities depend on stable IIO sysfs layout, scan-element naming conventions, and libc directory/file APIs. They are integrated by `iio_generic_buffer`, `iio_event_monitor`, and `lsiio`, and the header exposes their contracts.

## Risks and Test Signals

Several functions assume filenames have expected suffix lengths before subtracting suffix lengths; unusual sysfs entries could stress those assumptions. String reads use `%s`, so names with whitespace are truncated. `find_type_by_name` skips entries with colon after the numeric suffix to avoid char devices. Tests should use fake sysfs trees for channel parsing, scale/offset fallback, enabled-channel counting, sorting, verified write mismatch, and error cleanup, plus live tests against real IIO devices.
