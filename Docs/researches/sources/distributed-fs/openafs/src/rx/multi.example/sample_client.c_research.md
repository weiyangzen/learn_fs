# sources/distributed-fs/openafs/src/rx/multi.example/sample_client.c

Purpose: demonstrates Rx `multi_Rx` parallel calls across up to 50 hosts.

Important APIs/types/functions: `GetIpAddress` and `main`, generated `multi_TEST_Add`, `multi_Rx`, `multi_End`, `multi_Abort`, and variables `multi_i`/`multi_error`.

Control flow: parses `-verbose`, `-count`, and `-abort`, resolves hostnames, initializes Rx/null security, creates one connection per host, then for each trial runs a multi-call block that invokes `TEST_Add` on all connections in parallel and counts successes.

State/persistence: no durable state; maintains host arrays, argument array, connection array, and success counters.

Dependencies/integration: generated `sample.h`, Rx multi-call macros, Rx clock utilities, DNS, and null security.

Risks: argument parsing dereferences `**argv` without checking empty argc; arrays cap at 50 without bounds enforcement; uses `fprintf` incorrectly for unknown option; throughput timing can divide by zero when trials is zero. Test signals are multi-host successful adds, induced host failure with and without `-abort`, and count/verbose behavior.
