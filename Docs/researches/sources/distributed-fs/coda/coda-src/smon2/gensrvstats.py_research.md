# sources/distributed-fs/coda/coda-src/smon2/gensrvstats.py

Purpose: CGI script that generates RRDTool graph images for selected Coda server statistics and emits an HTML page referencing them.

Control flow: prints an HTML header, redirects stderr to stdout, parses CGI fields `servers`, `stats`, and `period`, validates server names against hardcoded `srvmap`, maps period keys through `timemap`, optionally enables logarithmic graphing, changes to `LOGDIR`, opens an `rrdtool -` pipe, and for each requested stat/server writes a graph command using `statmap` definitions and prints an `<IMG>` tag. Exceptions render a traceback in the HTML.

State/persistence: reads `.rrd` databases from `LOGDIR`, writes graph GIFs into `IMGDIR`, and emits HTTP response content. No authentication or mutable application state beyond generated images.

Dependencies, risks, tests: depends on deprecated Python `cgi`, hardcoded hosts/paths/RRDTool version, web-server permissions, and RRD data-source names matching `smon2.c`. Server validation mitigates command injection for server names, but `stat.value` is not checked before indexing `statmap` and may raise tracebacks. Test valid multi-server graphs, invalid server/stat/period, logscale mode, missing RRDTool, and web write permissions.
