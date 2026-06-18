# sources/cloud-native/moby/integration-cli/docker_cli_import_test.go

Purpose: integration tests for `docker import` from stdin, files, gzip files, bad URLs/nonexistent files, commit messages, and quoted `--change` instructions.

Important APIs/types/functions: `DockerCLIImportSuite`; tests `TestImportDisplay`, `TestImportBadURL`, `TestImportFile`, `TestImportGzipped`, `TestImportFileWithMessage`, `TestImportFileNonExistentFile`, and `TestImportWithQuotedChanges`.

Control flow: tests create or run a busybox container, export it to stdout or a temp file, optionally gzip the stream, import it, and run the resulting image. Message tests inspect `docker history` and parse the comment column. Quoted change tests import with `-c ENTRYPOINT ["/bin/sh", "-c"]` and run the result.

State and persistence: creates containers, temporary tar/gzip files, imported images, image history entries, and image config changes. Bad URL/file tests should not create usable images.

Dependencies and integration points: Docker export/import/history/run commands, gzip writer, shell pipeline helper, regex table parsing, network/DNS behavior for invalid URL errors, and Linux archive support.

Risks: accepted bad-URL error text is intentionally broad because systems can fail at different layers. History table parsing is format-sensitive. Import display tests assert exactly one newline, so CLI progress/output changes are caught.

Test signals: failures indicate regressions in import stream handling, decompression, import output format, imported image runnability, message/history persistence, error handling, or parsing of quoted `--change` directives.
