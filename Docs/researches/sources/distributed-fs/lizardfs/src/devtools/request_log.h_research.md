# sources/distributed-fs/lizardfs/src/devtools/request_log.h

Purpose: optional request latency logging and average aggregation instrumentation.

Important APIs/types/functions: under `ENABLE_REQUEST_LOG`, `RequestLogConfiguration` reads env options, `DummyRTTimer` tracks microsecond lifetimes, `Compressor` wraps gzip/bzip2/none output, `TuplePrinter` writes tab-separated tuples, singleton `RequestsLog` buffers slow requests and average stats, `FunctionCallLog` and `FunctionCallAvgLog` are RAII helpers, and macros log requests or averages until scope end. Without the flag, macros are no-ops and `DummyRTTimer` is empty.

Control flow: `RequestsLog::instance()` starts a background flushing thread. Calls below `REQUEST_THRESHOLD_MS` are ignored. Request and average data are swapped under mutexes into local collections by `Flusher`, then written periodically to `REQUESTS_LOG` and `REQUESTS_LOG.avg`.

State and persistence: process-global singleton keeps bounded request vector capacity and average map; background thread writes compressed or plain log files and joins on destruction.

Dependencies and integration: depends on Boost.Iostreams gzip/bzip2, threading, mutexes, atomics, `slogger`, `massert`, and `devtools/configuration.h`. Intended for instrumentation builds, not default runtime.

Risks: default `REQUESTS_TO_BE_LOGGED` reserves up to 40 million entries, explicitly warning about multi-GB RAM use. Logging thread starts during singleton initialization and writes to stdout/stderr. Destructor join can block up to the flush sleep interval. Compression algorithm errors call `mabort`.

Test signals: no direct tests; compile coverage requires `ENABLE_REQUEST_LOG` and Boost compression support.
