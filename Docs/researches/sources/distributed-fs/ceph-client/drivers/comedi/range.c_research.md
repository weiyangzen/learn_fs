# sources/distributed-fs/ceph-client/drivers/comedi/range.c

## Purpose
This file defines common COMEDI range tables and implements range metadata validation/copying for the `COMEDI_RANGEINFO` ioctl plus channel-list validation for subdevices.

## Important APIs, Types, And Functions
Exported range tables include `range_bipolar10`, `range_bipolar5`, `range_bipolar2_5`, `range_unipolar10`, `range_unipolar5`, `range_unipolar2_5`, current ranges `range_0_20mA`, `range_4_20mA`, `range_0_32mA`, and `range_unknown`. `do_rangeinfo_ioctl()` validates a `struct comedi_rangeinfo` request and copies the selected `struct comedi_krange` array to user memory. `comedi_check_chanlist()` validates channel and range indexes for each chanspec in a command or instruction.

## Control Flow
`do_rangeinfo_ioctl()` decodes subdevice and channel from `range_type`, verifies device attachment and subdevice bounds, selects either a shared `s->range_table` or per-channel `s->range_table_list`, verifies requested range length against the table length, and uses `copy_to_user()` to return the range array. `comedi_check_chanlist()` loops over each chanspec, resolves the correct range length from shared or per-channel range tables, and rejects any channel outside `s->n_chan` or range index outside the table length.

## State And Persistence
The range table objects are immutable exported constants. No mutable persistent state is owned by this file.

## Dependencies And Integration Points
The file depends on COMEDI chanspec macros (`CR_CHAN`, `CR_RANGE`, `RANGE_LENGTH`), COMEDI subdevice range-table conventions, Linux uaccess, and COMEDI logging. It is used by ioctl handling, command validation, and kernel-library instruction validation.

## Risks And Edge Cases
Only channel and range index are validated by `comedi_check_chanlist()`; analog reference and flags are intentionally left to drivers. `range_type` packs subdevice/channel/length in fixed bit positions and bad user values return `-EINVAL`. Per-channel range tables require valid channel bounds before indexing.

## Test Signals
Tests should cover shared and per-channel range tables, wrong range lengths, invalid subdevice/channel indexes, `copy_to_user()` faults, valid and invalid chanspec lists, and driver-specific validation for references/flags outside this helper.
