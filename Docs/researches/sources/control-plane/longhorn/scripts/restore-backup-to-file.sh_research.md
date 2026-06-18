# sources/control-plane/longhorn/scripts/restore-backup-to-file.sh

## Purpose
Runs the Longhorn engine container to restore a backup URL into a raw or qcow2 file under `/tmp/restore`.

## Important APIs and Variables
Flags include AWS credentials, CIFS credentials, `--backup-url`, `--output-file`, `--output-format`, `--version`, and optional `--backing-file`. It invokes `docker run ... longhornio/longhorn-engine:<version> longhorn backup restore-to-file`.

## Control Flow
The script parses flags and validates required backup URL, output file, output format, and Longhorn version. S3 URLs require AWS access key and secret. It builds Docker args: S3 gets AWS env vars; non-S3 gets Linux capabilities and apparmor relaxation; CIFS adds CIFS env vars. It mounts `/tmp/restore:/tmp/restore` and runs `restore-to-file` with output/backing-file options.

## State and Persistence
Writes the restored image file into the host `/tmp/restore` directory. Pulls or uses a Longhorn engine image by version. Does not change Kubernetes state.

## Dependencies and Integration Points
Requires Docker, Longhorn engine image availability, backupstore access, and host `/tmp/restore`. Integrates with Longhorn backup formats and S3/NFS/CIFS URL schemes.

## Risks
Credentials are exposed on the Docker command line/environment. The script validates S3 credentials but not CIFS credentials for CIFS URLs. Quoting around `backup_url` is awkward and can break URLs containing shell-special characters. Output file is forced under `/tmp/restore/${output_file}` even if the user supplies an absolute path. Privileged capabilities for non-S3 restores increase host risk.

## Test Signals
Restore a small known backup to raw and qcow2 and compare size/checksum or filesystem mountability. Test S3 and CIFS/NFS paths separately. Validate failure paths for missing credentials and invalid image versions.
