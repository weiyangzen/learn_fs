# sources/control-plane/external-snapshotter/release-tools/cloudbuild.sh

Purpose: generic Cloud Build entrypoint that delegates image build logic to release-tools `prow.sh`.

Important commands: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: shell loads shared Prow/release helper functions, then runs the Google Container Registry build helper.

State and persistence: build state and pushed images are managed by `gcr_cloud_build`; this wrapper creates no local state by itself.

Dependencies and integration: requires repositories to import release-tools and provide Cloud Build substitutions/environment expected by `prow.sh`.

Risks and test signals: risks are source path assumptions and failures hidden in sourced helper code. Signal is successful multi-arch Cloud Build image publication.
