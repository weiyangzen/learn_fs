# File Research: sources/cow-pools/nilfs-utils/lib/parser.c

Implements command-line parsing helpers. `nilfs_parse_cno()` rejects negative numbers before calling `strtoull()`. `nilfs_parse_cno_range()` accepts single checkpoint numbers and `..` range forms. `nilfs_parse_protection_period()` parses unsigned durations with suffixes for seconds, minutes, hours, days, weeks, months, and years.

It uses `NILFS_CNO_MAX` as an invalid/sentinel value and reports overflow through `ERANGE`.
