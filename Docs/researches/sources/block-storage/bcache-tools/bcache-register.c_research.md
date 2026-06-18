# File Research: sources/block-storage/bcache-tools/bcache-register.c

This small C helper takes exactly one argument, opens `/sys/fs/bcache/register` writable, and writes the argument plus newline with `dprintf`. It reports a clear error if the bcache kernel module is not loaded or registration fails.

It duplicates the registration logic later exposed by the broader `bcache register` command, but its small surface makes it suitable for udev execution.
