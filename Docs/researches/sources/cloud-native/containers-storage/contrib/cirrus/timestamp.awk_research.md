<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/timestamp.awk -->
# sources/cloud-native/containers-storage/contrib/cirrus/timestamp.awk

- Purpose: Prefixes CI log lines with elapsed time for easier diagnosis.
- Important behavior: Records `STARTTIME` in `BEGIN`, prints each input line with relative seconds, and prints total duration in `END`.
- Control flow and state: Stateless stream filter except for start timestamp.
- Dependencies and integration: Used by `.cirrus.yml` as `_TIMESTAMP` around setup/build/test scripts.
- Risks: Output buffering and awk implementation differences can affect live logs.
- Test signals: Cirrus logs show `[+NNNNs]` prefixes and END duration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/contrib/cirrus/timestamp.awk -->
