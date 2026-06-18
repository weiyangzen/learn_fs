# sources/cloud-native/moby/daemon/logger/splunk/splunk.go

Purpose: Splunk HTTP Event Collector logging driver.

Important APIs/types/functions: `New`, format wrappers `splunkLoggerInline`, `splunkLoggerJSON`, `splunkLoggerRaw`, `Log`, `queueMessageAsync`, `worker`, `postMessages`, `tryPostMessages`, `Close`, `ValidateLogOpt`, `parseURL`, `verifySplunkConnection`, and advanced env option parsers.

Control flow/state/persistence: `New` parses endpoint/token/TLS/CA/gzip/index-ack/format/tag/attrs, optionally verifies HEC with OPTIONS, builds an HTTP client and buffered stream, then starts a worker. Each `Log` converts a message into inline, json, or raw HEC event and enqueues it. Worker batches by size or timer, posts JSON events concatenated in one request, optionally gzip-compressed, and keeps failed messages until success, buffer maximum, or close. Close closes the stream and waits for final flush and transport cleanup.

Dependencies/integration: uses `logger.Info`, `loggerutils.ParseLogTag`, HTTP/TLS/x509, gzip, UUID request channels for index acknowledgment, and containerd logging for failed sends.

Risks: `queueMessageAsync` can block when stream is full. Failed delivery eventually logs and drops messages when buffer is exceeded or on last chance. TLS minimum version is explicitly FIXME. Raw format skips blank messages because HEC rejects them.

Test signals: Splunk tests outside this item cover validation, formats, batching/frequency, verification, retries, buffer maximum, close, and deadlock-on-blocked-endpoint behavior.
