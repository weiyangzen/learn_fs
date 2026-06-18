# sources/distributed-fs/coda/coda-src/norton/norton-rds.cc

Purpose: minimal command wrapper for printing RDS/RVM heap information from Norton.

API and flow: declares external `print_heap()` and exposes `show_heap(int, char **)`, which ignores arguments and calls `print_heap`.

Dependencies and risks: depends on the RDS heap implementation providing `print_heap`. There is no input validation because none is needed. Test signal is the interactive `show heap` command successfully linking and printing heap state.
