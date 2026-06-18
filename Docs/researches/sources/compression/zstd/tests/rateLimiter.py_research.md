# sources/compression/zstd/tests/rateLimiter.py

Purpose: This Python script is a minimal stdin-to-stdout throttler used as a replacement for `pv` in tests. It limits throughput to a caller-specified number of MB/s and intentionally does not "catch up" after blocking.

Important APIs and functions: The script has no function definitions. At module execution it reads `sys.argv[1]`, converts it to bytes per second using `MB = 1024 * 1024`, and loops over `sys.stdin.buffer.read()` and `sys.stdout.buffer.write()`. It catches `KeyboardInterrupt` and `BrokenPipeError` so pipelines can terminate without noisy tracebacks.

Control flow: It initializes `start = time.time()` and repeatedly computes how many bytes may be read since the previous iteration. `to_read` is at least one byte and capped to 1 MiB. It then resets `start` to the current time, reads up to `to_read`, writes the buffer, and exits once read returns an empty buffer.

State and persistence: State is transient: current timestamp, rate, and the current buffer. `total_read` is initialized but unused, so the limiter is interval-based rather than cumulative. It writes no files and has no persistent cache.

Dependencies and integration points: It depends only on Python standard modules `sys` and `time`. Test scripts can insert it in a pipe to simulate slow producers or consumers for zstd streaming behavior.

Risks and test signals: There is no argument validation, so missing or invalid rates raise Python exceptions. Because writes are not flushed explicitly and no sleep is used, low rates can still be affected by pipe buffering and scheduler timing. The unused `total_read` hints that cumulative accounting was considered but not implemented. Successful behavior is observable by bounded output throughput and clean exit on EOF or broken downstream pipe.
