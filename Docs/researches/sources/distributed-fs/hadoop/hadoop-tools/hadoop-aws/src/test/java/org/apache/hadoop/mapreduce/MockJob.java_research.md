<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/MockJob.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/MockJob.java


## Purpose
MapReduce Job subclass that replaces YARN/client submission with a Mockito ClientProtocol for unit tests needing JobSubmitter behavior.


## Important APIs, Types, and Functions
MockJob defines constructor, init(), isSuccessful(), package-private getJobSubmitter(), connect(), getSubmittedCredentials(), and updateStatus(). It stores mockClient, jobIdCounter/trackerId, and submittedCredentials.


## Control Flow
init() stubs submitJob to capture submitted credentials and return a RUNNING JobStatus, getNewJobID to return incrementing IDs, and getQueueAdmins to allow all. getJobSubmitter ignores the supplied submitClient and constructs a JobSubmitter with the mock client.


## State and Persistence Behavior
State includes static job ID/tracker counters and per-instance submitted credentials. No YARN cluster or real job execution occurs.


## Dependencies and Integration Points
Depends on Job, JobSubmitter package-private access, ClientProtocol, Mockito, Credentials, JobConf, and AccessControlList.


## Risks and Test Signals
Risks are package-private coupling to Hadoop MapReduce internals and static counter sharing. Signals let tests inspect submitted credentials/resources without contacting YARN.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/mapreduce/MockJob.java -->
