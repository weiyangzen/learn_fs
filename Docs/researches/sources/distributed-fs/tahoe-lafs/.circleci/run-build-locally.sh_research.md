## sources/distributed-fs/tahoe-lafs/.circleci/run-build-locally.sh

Purpose: legacy helper for triggering a CircleCI v1.1 build against a specific branch/config for local experimentation.

Important behavior: defines a hard-coded `CIRCLE_TOKEN`, posts current `git rev-parse HEAD`, `config.yml`, and `notify=false` to a CircleCI v1.1 project URL under `exarkun/tahoe-lafs`.

Control flow: a single `curl --user` call sends multipart form fields.

State and dependencies: no local persistence; creates remote CI activity. Depends on git, curl, and validity of the embedded token/API endpoint.

Risks: the hard-coded token is a clear secret-management concern and may be obsolete. The endpoint references a personal fork/branch path, so this script is likely historical and fragile.
